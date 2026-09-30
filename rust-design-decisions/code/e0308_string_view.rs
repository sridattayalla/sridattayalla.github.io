fn takes_owned(s: String) {
    println!("{s}");
}

fn main() {
    let view: &str = "hello";
    takes_owned(view);
}
