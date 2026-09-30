trait Shape {
    fn area(&self) -> f64;
}

struct Square(f64);
struct Circle(f64);

impl Shape for Square {
    fn area(&self) -> f64 {
        self.0 * self.0
    }
}

impl Shape for Circle {
    fn area(&self) -> f64 {
        3.141592653589793 * self.0 * self.0
    }
}

fn main() {
    let shapes: Vec<Box<dyn Shape>> = vec![Box::new(Square(2.0)), Box::new(Circle(1.0))];
    for shape in &shapes {
        println!("{:.2}", shape.area());
    }
    println!("&dyn Shape size: {}", std::mem::size_of::<&dyn Shape>());
    println!("&[u32] size: {}", std::mem::size_of::<&[u32]>());
    println!("&Square size: {}", std::mem::size_of::<&Square>());
}
