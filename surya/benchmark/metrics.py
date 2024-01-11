def intersection_area(box1, box2):
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    return (x_right - x_left) * (y_bottom - y_top)


def intersection_pixels(box1, box2):
    x_left = max(box1[0], box2[0])
    y_top = max(box1[1], box2[1])
    x_right = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])

    if x_right < x_left or y_bottom < y_top:
        return set()

    pixels = set()
    for x in range(int(x_left), int(x_right)):
        for y in range(int(y_top), int(y_bottom)):
            pixels.add((x, y))

    return pixels


def calculate_coverage(box, other_boxes):
    box_area = (box[2] - box[0]) * (box[3] - box[1])
    if box_area == 0:
        return 0

    # find total coverage of the box
    covered_pixels = set()
    double_coverage = 0
    for other_box in other_boxes:
        ia = intersection_pixels(box, other_box)
        covered_pixels_len = len(covered_pixels)
        covered_pixels = covered_pixels.union(ia)

        # We want to penalize overlapping a region twice, since this can lead to inaccurate OCR
        double_coverage += (len(ia) + covered_pixels_len) - len(covered_pixels)

    covered_pixels_count = max(0, len(covered_pixels) - double_coverage)
    return covered_pixels_count / box_area


def precision_recall(preds, references, threshold=.5):
    if len(references) == 0:
        return {
            "precision": 1,
            "recall": 1,
        }

    if len(preds) == 0:
        return {
            "precision": 0,
            "recall": 0,
        }

    iou = []
    for box1 in preds:
        coverage = calculate_coverage(box1, references)
        iou.append(coverage)

    classes = [1 if i > threshold else 0 for i in iou]
    precision = sum(classes) / len(classes)

    iou = []
    for box1 in references:
        coverage = calculate_coverage(box1, preds)
        iou.append(coverage)

    classes = [1 if i > threshold else 0 for i in iou]
    recall = sum(classes) / len(classes)

    return {
        "precision": precision,
        "recall": recall,
    }


def mean_coverage(preds, references):
    coverages = []
    for box1 in references:
        coverage = calculate_coverage(box1, preds)
        coverages.append(coverage)

    for box2 in preds:
        coverage = calculate_coverage(box2, references)
        coverages.append(coverage)

    # Calculate the average coverage over all comparisons
    if len(coverages) == 0:
        return 0
    coverage = sum(coverages) / len(coverages)
    return {"coverage": coverage}