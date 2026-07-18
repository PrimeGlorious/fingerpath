import cv2

from vision.camera import Camera


def main() -> None:
    camera = Camera()

    try:
        while True:
            frame = camera.read()
            mirrored_frame = cv2.flip(frame, 1)

            cv2.imshow("Fingerpath Camera", mirrored_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
