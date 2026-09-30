fn split_at_mut(slice: &mut [i32]) -> (&mut [i32], &mut [i32]) {
    let mid = slice.len() / 2;
    (&mut slice[..mid], &mut slice[mid..])
}

fn main() {
    let mut data = vec![1, 2, 3, 4, 5, 6];
    let (a, b) = split_at_mut(&mut data);
    a[0] = 100;
    b[0] = 200;
    println!("{:?}", data);
}
