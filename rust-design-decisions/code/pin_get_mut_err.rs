use std::marker::PhantomPinned;
use std::pin::Pin;

struct SelfRef {
    data: String,
    _pin: PhantomPinned,
}

fn main() {
    let pinned = Pin::from(Box::new(SelfRef {
        data: "hello".to_string(),
        _pin: PhantomPinned,
    }));
    let whole: &mut SelfRef = pinned.get_mut();
    whole.data.clear();
}
