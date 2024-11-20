extern crate session_types;
use session_types::*;

type SignExtender = Recv<i8, Offer<Send<i8, Eps>, Send<i16, Eps>>>;

type Client = Send<i8, Choose<Recv<i8, Eps>, Recv<i16, Eps>>>;


// A module which either returns the i8
// or the sign-extended value as an i16.
fn srv(c: Chan<(), SignExtender>) {
    let (c, value) = c.recv();
    match c.offer() {
        Branch::Left(c) => {
            c.send(value).close();
        },
        Branch::Right(c) => {
            c.send(value.into()).close();
        }
    }
}

fn cli_i8(c: Chan<(), Client>) {
    let n = -1;
    let c = c.send(n);
    let c = c.sel1();
    let (c, value) = c.recv();


    print_type_of(&value);
    println!("{value}");

    c.close();
}

fn cli_i16(c: Chan<(), Client>) {
    let n = -54;
    let c = c.send(n);
    let c = c.sel2();
    let (c, value) = c.recv();

    print_type_of(&value);
    println!("{value}");

    c.close();
}

fn main() {
    connect(srv, cli_i8);
    connect(srv, cli_i16);
}

fn print_type_of<T>(_: &T) {
    println!("{}", std::any::type_name::<T>());
}
