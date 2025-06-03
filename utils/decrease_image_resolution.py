import cv2

def resize_image_to_long_side(img_path, long_side=640):
    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    if h > w:
        scale = long_side / h
        new_dim = (int(w * scale), long_side)
    else:
        scale = long_side / w
        new_dim = (long_side, int(h * scale))

    resized = cv2.resize(img, new_dim, interpolation=cv2.INTER_AREA)
    return resized

resized_img = resize_image_to_long_side("image.jpg")
cv2.imwrite("resized.jpg", resized_img)
