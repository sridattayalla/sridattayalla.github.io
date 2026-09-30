fn main() {
    let mut v = vec![10, 20, 30];
    let first = &v[0];
    println!("first {first}");
    v.push(40);
    println!("len {}", v.len());
}
