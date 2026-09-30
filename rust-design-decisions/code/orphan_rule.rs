use std::fmt;

impl fmt::Display for Vec<u8> {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Vec<u8> of {} bytes", self.len())
    }
}

fn main() {
    let v = vec![1, 2, 3];
    println!("{}", v);
}
