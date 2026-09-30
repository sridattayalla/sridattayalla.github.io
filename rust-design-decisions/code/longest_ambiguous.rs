fn longest(a: &str, b: &str) -> &str {
    if a.len() > b.len() { a } else { b }
}
fn main() {
    let w = longest("alpha", "beta");
    println!("{w}");
}
