extern crate session_types;
use session_types::*;

type Server = Recv<i64, Send<bool, Eps>>;
type Client = Send<i64, Recv<bool, Eps>>;

fn srv(c: Chan<(), Server>) {
    let (c, n) = c.recv();
    if n % 2 == 0 {
        c.send(true).close()
    } else {
        c.send(false).close()
    }
}

fn cli(c: Chan<(), Client>) {
    let n = 42;
    let c = c.send(n);
    let (c, b) = c.recv();

    if b {
        println!("{n} is even");
    } else {
        println!("{n} is odd");
    }

    c.close();
}

fn main() {
    connect(srv, cli);
}
