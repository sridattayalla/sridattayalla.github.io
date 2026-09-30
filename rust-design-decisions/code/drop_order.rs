struct PrintOnDrop(&'static str);
impl Drop for PrintOnDrop {
    fn drop(&mut self) { println!("drop {}", self.0); }
}
struct Pair { one: PrintOnDrop, two: PrintOnDrop }
fn main() {
    let a = PrintOnDrop("a-first");
    let b = PrintOnDrop("b-second");
    let p = Pair { one: PrintOnDrop("one"), two: PrintOnDrop("two") };
    {
        let c = PrintOnDrop("c-inner");
        println!("end of inner scope");
    }
    println!("end of main");
}
