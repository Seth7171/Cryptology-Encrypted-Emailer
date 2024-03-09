import random
import hashlib
import math

class SignatureScheme:
    def __init__(self, bits=1024, seed=117):
        self.primes = self.generate_primes(10 ** 7)
        random.seed(seed)
        self.p = self.get_prime(bits)
        self.q = self.get_prime(bits)
        self.n = self.p * self.q
        self.b = 10 ** 9 + 7
        self.d = self.b * pow(2, (self.p - 1) * (self.q - 1) - 1, self.n)

    def get_public_key(self):
        return self.n, self.d

    def get_random_string(self, size):
        return ''.join(str(random.randint(0, 1)) for _ in range(size))

    def get_hash_value(self, string):
        return int.from_bytes(hashlib.sha256(string.encode()).digest(), 'big')

    def is_quadratic_residue(self, val, prime):
        return 1 == pow(val, (prime - 1) // 2, prime)

    def get_signature(self, message):
        U = self.get_random_string(60)
        c = self.get_hash_value(message + U)
        m = c + self.d * self.d

        while not (self.is_quadratic_residue(m, self.p) and self.is_quadratic_residue(m, self.q)):
            U = self.get_random_string(60)
            c = self.get_hash_value(message + U)
            m = c + self.d * self.d

        v1 = pow(m, (self.p + 1) // 4, self.p) * self.q * pow(self.q, self.p - 2, self.p)
        v2 = pow(m, (self.q + 1) // 4, self.q) * self.p * pow(self.p, self.q - 2, self.q)
        y = (v1 + v2) % self.n
        x = (y - self.d) % self.n
        return U, x

    def verify(self, signature, message):
        c = self.get_hash_value(message + signature[0])
        x = signature[1]
        l_side = x * (x + self.b)
        r_side = c
        return l_side % self.n == r_side % self.n

    def witness(self, a, k, m, prime_candidate):
        b = pow(a, m, prime_candidate)
        if b == 1:
            return False

        for _ in range(k):
            if (-1 % prime_candidate) == (b % prime_candidate):
                return False
            b = (b * b) % prime_candidate
        return True

    def initial_check(self, prime_candidate):
        for prime in self.primes:
            if prime_candidate % prime == 0:
                return False
        return True

    def miller_rabin_test(self, prime_candidate):
        if not self.initial_check(prime_candidate):
            return False

        temp = prime_candidate - 1
        k = 0
        while temp % 2 == 0:
            temp //= 2
            k += 1
        m = temp

        for _ in range(70):
            a = random.randint(2, prime_candidate - 2)
            if self.witness(a, k, m, prime_candidate):
                return False
        return True

    def get_prime_candidate(self, bits):
        prime_candidate = random.randint(2 ** (bits - 1), (2 ** bits) - 1)
        if prime_candidate % 2 == 0:
            prime_candidate += 1
        return prime_candidate

    def get_prime(self, bits):
        prime_candidate = self.get_prime_candidate(bits)
        while not self.miller_rabin_test(prime_candidate):
            prime_candidate = self.get_prime_candidate(bits)
        return prime_candidate

    def generate_primes(self, limit):
        is_prime = [True] * (limit + 1)
        primes = []
        for i in range(2, limit + 1):
            if is_prime[i]:
                primes.append(i)
                for j in range(i*i, limit + 1, i):
                    is_prime[j] = False
        return primes