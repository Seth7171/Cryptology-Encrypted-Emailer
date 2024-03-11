import random
import env
from sympy import nextprime


class ElgamalEncryption:
    def __init__(self, n=None, base_point_x=None, base_point_y=None, end_point_x=None, end_point_y=None):
        # self.n = n if n is not None else random.randint(5000, 9999)
        self.n = n if n is not None else self.get_random_prime()
        self.a = random.randint(10, 9999)
        self.b = random.randint(10, 9999)
        self.LHS = [[], []]
        self.RHS = [[], []]
        self.generate_polynomial()
        self.arr_x, self.arr_y = [], []
        self.count = self.generate_points()
        # self.base_point_x = self.arr_x[0]
        self.base_point_x = base_point_x if base_point_x is not None else self.arr_x[0]
        # self.base_point_y = self.arr_y[0]
        self.base_point_y = base_point_y if base_point_y is not None else self.arr_y[0]
        self.d = random.randint(315, self.n)
        while self.d >= self.n:
            self.d = random.randint(315, self.n)
        # self.end_point_x = self.d * self.base_point_x
        self.end_point_x = end_point_x if end_point_x is not None else self.d * self.base_point_x
        # self.end_point_y = self.d * self.base_point_y
        self.end_point_y = end_point_y if end_point_y is not None else self.d * self.base_point_y

    def get_elgamal_key(self):
        return [self.base_point_x, self.base_point_y, self.end_point_x, self.end_point_y, self.n]

    def generate_polynomial(self):
        for i in range(self.n):
            self.LHS[0].append(i)
            self.LHS[1].append((i ** 3 + self.a * i + self.b) % self.n)
            self.RHS[0].append(i)
            self.RHS[1].append((i ** 2) % self.n)

    def generate_points(self):
        count = 0
        for i in range(self.n):
            for j in range(self.n):
                if self.LHS[1][i] == self.RHS[1][j]:
                    count += 1
                    self.arr_x.append(self.LHS[0][i])
                    self.arr_y.append(self.RHS[0][j])
        return count

    @staticmethod
    def string_to_int(message):
        return int.from_bytes(message.encode('utf-8'), 'big')

    @staticmethod
    def int_to_string(integer):
        num_bytes = (integer.bit_length() + 7) // 8
        integer_bytes = integer.to_bytes(num_bytes, 'big')
        return integer_bytes.decode('utf-8')

    def encrypt(self, message):
        m = message
        k = random.randint(315, self.n)
        while k >= self.n:
            k = random.randint(315, self.n)
        C1x = k * self.base_point_x
        C1y = k * self.base_point_y
        if env.debug:
            print(f"Value of Cipher text 1 i.e. C1: ({C1x}, {C1y})\n")
        C2x = k * self.end_point_x + m
        C2y = k * self.end_point_y + m
        if env.debug:
            print(f"Value of Cipher text 2 i.e. C2: ({C2x}, {C2y})\n")
        return C1x, C1y, C2x, C2y

    def decrypt(self, C1x, C1y, C2x, C2y):
        Mx = C2x - self.d * C1x
        My = C2y - self.d * C1y
        if env.debug:
            print(f"The message received by receiver is: {Mx}")
        decrypted_message = Mx
        if env.debug:
            print(f"Decrypted message received by receiver is: {decrypted_message}")
        return decrypted_message


    def get_random_prime(self, lower_bound=314, upper_bound=9999):
        random_number = random.randint(lower_bound, upper_bound)
        random_prime = nextprime(random_number)

        # Ensure the prime number is within the upper bound
        if random_prime > upper_bound:
            # If the generated prime is greater than upper_bound, find the previous prime before upper_bound
            random_prime = nextprime(upper_bound, ith=-1)

        return random_prime



# Example usage
# ecc = ElgamalEncryption()
# print("Enter the message to be sent:\n")
# message = input()
# C1x, C1y, C2x, C2y = ecc.encrypt(message)
# ecc.decrypt(C1x, C1y, C2x, C2y)
