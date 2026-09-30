#[derive(Copy, Clone)]
struct Point(i32);

fn main() {
    let a = 5;
    let b = a;
    println!("a={} b={}", a, b);
    let p = Point(1);
    let q = p;
    println!("p={} q={}", p.0, q.0);
    let arr = [7, 8, 9];
    let _copy = arr[2];
    println!("inner still: {}", arr[2]);
}
