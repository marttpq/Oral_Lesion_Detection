class Animal:
    def __init__(self, name, sound):
        self.name = name
        self.sound = sound

    def make_sound(self):
        print(f"{self.name} says {self.sound}")

class Dog(Animal):
    def __init__(self, sound):
        super().__init__(sound, "woof1")

class Cat(Animal):
    def __init__(self, name,sound):
        super().__init__(name,sound)

animals = [Dog("Buddy"), Cat("Milo", "mew")]

for animal in animals:
    animal.make_sound()
