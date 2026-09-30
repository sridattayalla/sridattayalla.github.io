#[derive(Copy, Clone)]
struct Owner { name: &'static str, scores: Vec<i32> }
fn main() {
    let o = Owner { name: "ann", scores: vec![90, 95] };
    let p = o;
    println!("{}", p.name);
}
