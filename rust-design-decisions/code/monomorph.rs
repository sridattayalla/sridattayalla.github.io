fn largest<T: PartialOrd>(list: &[T]) -> &T {
    let mut max = &list[0];
    for item in list {
        if item > max {
            max = item;
        }
    }
    max
}

fn main() {
    let numbers = vec![3, 9, 2, 7];
    let words = vec!["apple", "banana", "pear", "fig"];
    println!("max n: {}", largest(&numbers));
    println!("max s: {}", largest(&words));
}
