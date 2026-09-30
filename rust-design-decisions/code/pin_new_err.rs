use std::marker::PhantomPinned;
use std::pin::Pin;

struct SelfRef {
    data: String,
    _pin: PhantomPinned,
}

fn main() {
    let value = SelfRef {
        data: "hello".to_string(),
        _pin: PhantomPinned,
    };
    let pinned = Pin::new(&value);
    println!("pinned a stack value: {}", pinned.get_ref().data);
}
