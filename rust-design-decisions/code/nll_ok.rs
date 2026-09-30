fn main() {
    let mut v = vec![1, 2, 3];
    for x in &v {
        println!("{x}");
    }
    v.push(4);
    println!("len {}", v.len());
}
