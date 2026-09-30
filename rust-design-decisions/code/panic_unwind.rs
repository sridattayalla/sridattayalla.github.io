use std::panic;

struct Dropped(&'static str);

impl Drop for Dropped {
    fn drop(&mut self) {
        println!("dropping {}", self.0);
    }
}

fn main() {
    let result = panic::catch_unwind(|| {
        let _first = Dropped("first");
        let _second = Dropped("second");
        panic!("boom");
    });
    println!("caught: {:?}", result);
    println!("main still running");
}
