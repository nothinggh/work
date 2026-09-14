# AND, OR, XOR, NOT 연산에 대해서 확인해보자.

import cv2

src1 = cv2.imread("my_input.jpg", cv2.IMREAD_COLOR)
src2 = cv2.imread("my_input1.jpg", cv2.IMREAD_COLOR)

if src1 is None or src2 is None:
    raise FileNotFoundError("이미지 파일을 찾을 수 없습니다. 경로를 확인하세요.")

# src2의 크기를 src1의 크기(너비, 높이)와 동일하게 변경
src2 = cv2.resize(src2, (src1.shape[1], src1.shape[0]))

dst_and = cv2.bitwise_and(src1, src2)
dst_or = cv2.bitwise_or(src1, src2)
dst_xor = cv2.bitwise_xor(src1, src2)
dst_not = cv2.bitwise_not(src1)

cv2.imshow("src1", src1)
cv2.imshow("src2", src2)
cv2.imshow("dst_and", dst_and)
cv2.imshow("dst_or", dst_or)
cv2.imshow("dst_xor", dst_xor)
cv2.imshow("dst_not", dst_not)

cv2.waitKey(0)
cv2.destroyAllWindows()
