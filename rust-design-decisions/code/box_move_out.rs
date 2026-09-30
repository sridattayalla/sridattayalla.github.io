fn main() {
    let b = Box::new(String::from("hello"));
    let s = *b;
    println!("{s}");
}
