extern crate session_types;
use session_types::*;

// Consider the language {bool^n u8^n | n >= 0}.

// We can construct a session type such that limits the set of invalid messages.
// Even though session types cannot fully express DPDAs,
// the fact that we're restricting our possible inputs reduces the code
// size and the number of cases a designer must consider!

// Note: if we choose an arbitrary recursion limit, it is possible to fully
// specify a session type to model any DPDA (up to that recursion limit).
// (This is trivial, as it's just converting it into a FSM.)
//
// We're not using that here. Instead, we're using session types only to
// prevent any bools from being sent after a u8.
// Then, we have a counter to verify that the number of bools and u8s match up.

type Server = Rec<Offer<
    Recv<bool, Var<Z>>,
    Rec<Offer<
        Recv<u8, Var<Z>>,
        Send<bool, Eps>  // send whether the string was in the language or not.
    >>
>>;
type Client = <Server as HasDual>::Dual;


// A module which either returns the i8
// or the sign-extended value as an i16.
fn srv(c: Chan<(), Server>) {
    let mut c = c.enter();

    let mut num_bool = 0;
    loop {
        c = match c.offer() {
            Branch::Left(c) => {
                let (c, _) = c.recv();
                num_bool += 1;
                c.zero()
            },
            Branch::Right(c) => {
                let mut c = c.enter();
                let mut num_u8 = 0;
                loop {
                    c = match c.offer() {
                        Branch::Left(c) => {
                            let (c, _) = c.recv();
                            num_u8 += 1;
                            c.zero()
                        },
                        Branch::Right(c) => {
                            let c = c.send(num_bool == num_u8);
                            c.close();
                            return;
                        }
                    }
                }
            }
        }
    }
}

fn client_valid_0(c: Chan<(), Client>) {
    let c = c.enter().sel2();
    let c = c.enter().sel2();

    let (c, is_valid) = c.recv();
    println!("client_valid_0: {is_valid}");

    c.close();
}

fn client_valid_1(c: Chan<(), Client>) {
    let c = c.enter()
        .sel1().send(true).zero()
        .sel1().send(true).zero()
        .sel2().enter()
        .sel1().send(1).zero()
        .sel1().send(1).zero()
        .sel2();

    let (c, is_valid) = c.recv();
    println!("client_valid_1: {is_valid}");

    c.close();
}

fn client_invalid_0(c: Chan<(), Client>) {
    let c = c.enter()
        .sel1().send(true).zero()
        .sel1().send(true).zero()
        .sel2().enter()
        .sel1().send(1).zero()
        .sel2();

    let (c, is_valid) = c.recv();
    println!("client_invalid_0: {is_valid}");

    c.close();
}

fn main() {
    connect(srv, client_valid_0);
    connect(srv, client_valid_1);
    connect(srv, client_invalid_0);
}
