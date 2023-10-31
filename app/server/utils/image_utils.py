import cv2
import numpy as np


def compress_image_bytes(image_bytes: bytes, compression_quality: int) -> bytes:
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), compression_quality]
    image = np.asarray(bytearray(image_bytes), dtype='uint8')
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    return cv2.imencode('.jpg', image, encode_param)[1].tobytes()


def image_to_thumbs(image, sizes: list[float]):
    """Creates image thumbnails for defined number of sizes

    Args:
        image (numpy.ndarray): image buffer
        sizes (list): images sizes

    Returns:
        [list]: image thumbnails
    """
    height, width, _channels = image.shape
    # un-comment if you need original thumb as well
    # thumbs = {"original": img}
    thumbs = {}
    for size in sizes:
        # if (width >= size):
        ratio = (size + 0.0) / width
        max_size = (size, int(height * ratio))
        thumbs[f'{max_size[0]}x{max_size[1]}'] = cv2.resize(image, max_size, interpolation=cv2.INTER_AREA)
    return thumbs


def image_to_thumbs_from_bytes(image_bytes: bytes, sizes: list[float]) -> dict[str, bytes]:
    """Creates image thumbnails for defined number of sizes

    Args:
        input_file (str): original image file path
        output_file (str): output image file path
        sizes (list): images sizes

    Returns:
        list: list of thumbnails paths
    """
    image = np.asarray(bytearray(image_bytes), dtype='uint8')
    # use imdecode function
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    thumbs = image_to_thumbs(image, sizes)
    thumbnails = {}
    for size, image in thumbs.items():
        image_bytes = cv2.imencode('.jpg', image)[1].tobytes()
        thumbnails[size] = image_bytes
    return thumbnails


def image_thumbnail(input_file: str, output_file: str, sizes: list[float]):
    """Creates image thumbnails for defined number of sizes

    Args:
        input_file (str): original image file path
        output_file (str): output image file path
        sizes (list): images sizes

    Returns:
        list: list of thumbnails paths
    """
    image = cv2.imread(input_file)
    thumb = image_to_thumbs(image, sizes)
    thumbnails = []
    for size, image in thumb.items():
        thumb_path = output_file % '_thumb_%s' % size
        cv2.imwrite(output_file % '_thumb_%s' % size, image)
        thumbnails.append(thumb_path)
    return thumbnails
