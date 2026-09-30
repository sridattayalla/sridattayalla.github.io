fn takes_view(s: &str) -> usize {
    s.len()
}

fn main() {
    let owned = String::from("hello");
    let view: &str = &owned;
    println!("view len {}", takes_view(view));
    println!("coerced len {}", takes_view(&owned));

    let v = vec![10, 20, 30];
    let middle: &[i32] = &v[1..3];
    println!("middle {:?} len {}", middle, middle.len());
}
