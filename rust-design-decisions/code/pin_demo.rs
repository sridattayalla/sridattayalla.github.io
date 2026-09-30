use std::marker::PhantomPinned;
use std::pin::Pin;
struct SelfRef {
    data: String,
    ptr: *const String,
    _pin: PhantomPinned,
}
impl SelfRef {
    fn report(self: Pin<&Self>) -> (usize, usize) {
        let field = &self.data as *const String as usize;
        let held = self.ptr as usize;
        // SAFETY: ptr was aimed at data before the value was pinned,
        // and Pin guarantees the value has not moved since.
        let text = unsafe { &*self.ptr };
        println!("field at {:#x}, stored pointer {:#x}, \"{}\"", field, held, text);
        (field, held)
    }
}
fn main() {
    let mut boxed = Box::new(SelfRef { data: "hello".to_string(), ptr: std::ptr::null(), _pin: PhantomPinned });
    // Creating the pointer is safe; following it is the audited part.
    // The address stays valid: a Box never moves its pointee.
    boxed.ptr = &boxed.data as *const String;
    let pinned = Pin::from(boxed);
    let before = pinned.as_ref().report();
    let moved = pinned;
    let after = moved.as_ref().report();
    assert_eq!(before, after);
    println!("addresses unchanged: the handle moved, the value did not");
}
