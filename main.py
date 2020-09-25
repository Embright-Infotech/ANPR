import random
import os
import cv2
import time
import utils
import argparse
from ctypes import *
from queue import Queue
from threading import Thread, enumerate
from openalpr import Alpr

# 1920x1080 yields the best results
rev_width = 1920
rev_height = 1080

def parser():
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default="test1.mp4",
                        help="video source. If empty, uses webcam 0 stream")
    parser.add_argument("--out_filename", type=str, default="output.avi",
                        help="inference video name. Not saved if empty")
    parser.add_argument("--weights", default="custom/yolov4-tiny-custom_last.weights",
                        help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true',
                        help="windown inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true',
                        help="display bbox coordinates of detected objects")
    parser.add_argument("--config_file", default="custom/yolov4-tiny.cfg",
                        help="path to config file")
    parser.add_argument("--data_file", default="custom/obj.data",
                        help="path to data file")
    parser.add_argument("--thresh", type=float, default=.25,
                        help="remove detections with confidence below this value")
    return parser.parse_args()


def str2int(video_path):
    """
    argparse returns and string althout webcam uses int (0, 1 ...)
    Cast to int if needed
    """
    try:
        return int(video_path)
    except ValueError:
        return video_path

# Convert YOLO returned coordinates
def convertBack(x,y,w,h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    if str2int(args.input) == str and not os.path.exists(args.input):
        raise(ValueError("Invalid video path {}".format(os.path.abspath(args.input))))


def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    fps = int(input_video.get(cv2.CAP_PROP_FPS))
    video = cv2.VideoWriter(output_video, fourcc, fps, size)
    return video


def video_capture(frame_queue, darknet_image_queue):
    while cap.isOpened():
        ret, frame = cap.read()
        global rev_height
        global rev_width
        rev_height, rev_width = frame.shape[:2]
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_default = frame_rgb
        frame_default_queue.put(frame_default)
        frame_resized = cv2.resize(frame_rgb, (width, height),
                                   interpolation=cv2.INTER_LINEAR)
        frame_queue.put(frame_resized)
        d_test.copy_image_from_bytes(darknet_image, frame_resized.tobytes())
        darknet_image_queue.put(darknet_image)
    cap.release()


def inference(darknet_image_queue, detections_queue, fps_queue):
    while cap.isOpened():
        darknet_image = darknet_image_queue.get()
        prev_time = time.time()
        detections = d_test.detect_image(network, class_names, darknet_image, thresh=args.thresh)
        detections_queue.put(detections)
        fps = int(1/(time.time() - prev_time))
        fps_queue.put(fps)
        print("FPS: {}".format(fps))
        d_test.print_detections(detections, args.ext_output)
    cap.release()

def drawing(frame_queue, detections_queue, fps_queue):
    random.seed(3)  # deterministic bbox colors
    video = set_saved_video(cap, args.out_filename, (rev_width, rev_height))
    while cap.isOpened():
        frame_default = frame_default_queue.get()
        frame_resized = frame_queue.get()
        detections = detections_queue.get()
        fps = fps_queue.get()
        if frame_resized is not None:
            image = d_test.draw_boxes(detections, frame_default, class_colors, width, height, rev_width, rev_height)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            if args.out_filename is not None:
                video.write(image)
            if not args.dont_show:
                cv2.namedWindow('Inference',cv2.WINDOW_NORMAL)
                cv2.resizeWindow('Inference', (1920,1080))
                cv2.imshow('Inference', image)
            if cv2.waitKey(fps) == 27:
                break
    cap.release()
    video.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':

    # Initialize Alpr
    alpr = Alpr("us","/etc/openalpr/openalpr.conf",\
                "/usr/share/openalpr/runtime_data/")

    # Check for errors when loading Alpr
    if not alpr.is_loaded():
        print("Error loading OpenALPR")
        sys.exit(1)

    frame_queue = Queue()
    frame_default_queue = Queue()
    darknet_image_queue = Queue(maxsize=1)
    detections_queue = Queue(maxsize=1)
    fps_queue = Queue(maxsize=1)

    args = parser()
    check_arguments_errors(args)
    network, class_names, class_colors = d_test.load_network(
            args.config_file,
            args.data_file,
            args.weights,
            batch_size=1
        )
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = d_test.network_width(network)
    height = d_test.network_height(network)
    darknet_image = d_test.make_image(width, height, 3)
    input_path = str2int(args.input)
    cap = cv2.VideoCapture(input_path)
    Thread(target=video_capture, args=(frame_queue, darknet_image_queue)).start()
    Thread(target=inference, args=(darknet_image_queue, detections_queue, fps_queue)).start()
    Thread(target=drawing, args=(frame_queue, detections_queue, fps_queue)).start()
