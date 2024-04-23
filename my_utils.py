import numpy as np

def same_sign(num1, num2):
    # Przesunięcie bitowe o 31 bity w lewo - dostaniemy 1 dla liczby ujemnej i 0 dla liczby nieujemnej
    # sign1 = (num1 >> 31) & 1
    # sign2 = (num2 >> 31) & 1
    sign1 = np.sign(num1)
    sign2 = np.sign(num2)
    # Porównanie bitów znaku
    return sign1 == sign2


# Define a function to rotate a vector
def rotate_vector(vector, angle_radians):
    # Define the rotation matrix
    rotation_matrix = np.array([[np.cos(angle_radians), -np.sin(angle_radians)],
                                [np.sin(angle_radians), np.cos(angle_radians)]])

    # Rotate the vector
    rotated_vector = np.dot(rotation_matrix, vector)

    return rotated_vector