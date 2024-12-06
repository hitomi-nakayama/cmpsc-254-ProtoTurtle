extern crate session_types;
use session_types::*;


/// This module receives either u8 or i16 and adds them to an internal
/// accumulator.
/// It loops indefinitely until the client decides to receive the accumulated
/// result.
/// After sending the result, the session is terminated.
type Accumulator = Rec<Offer<  // client chooses whether to send more data or
                               // get result back from accumulator.
    Offer<  // client chooses between sending u8 or i16.
        Recv<u8, Var<Z>>,  // take u8 and jump back to loop
        Recv<i16, Var<Z>>  // take i16 and jump back to loop
    >,
    Send<i16, Eps>  // return the accumulated result and end session
>>;

/// The Client is the dual of the Accumulator module.
type Client = <Accumulator as HasDual>::Dual;


// A module which either returns the i8
// or the sign-extended value as an i16.
fn srv(c: Chan<(), Accumulator>) {

    let mut accumulator: i16 = 0;
    let mut c = c.enter();  // enter loop
    loop {
        c = match c.offer() {  // allow the client to choose between sending
                               // more addends or recieveng the result and
                               // terminating.
            Branch::Left(c) => {
                match c.offer() {  // allow the client to choose between
                                   // sending a u8 or i16.
                    Branch::Left(c) => {
                        // receive a u8
                        let (c, addend) = c.recv();

                        let addend: i16 = addend.into();
                        accumulator += addend;

                        // put session state at beginning of loop
                        c.zero()
                    },
                    Branch::Right(c) => {
                        // receive an i16
                        let (c, addend) = c.recv();
                        accumulator += addend;
                        c.zero()
                    }
                }
            },
            Branch::Right(c) => {
                // send the result and terminate session
                c.send(accumulator).close();
                break
            }
        }
    }
}


/// This example sends no data and receives the result.
fn client_0(c: Chan<(), Client>) {
    let c = c.enter();  // enter loop

    // get accumulator value
    let c = c.sel2();
    let (c, accumulator) = c.recv();
    assert_eq!(0, accumulator);

    c.close();
}


/// this example sends one u8 and one i16.
fn client_1(c: Chan<(), Client>) {
    let c = c.enter();  // enter loop

    let c = c.sel1();  // send addend
    let c = c.sel1();  // send u8
    let c = c.send(10u8);
    let c = c.zero();  // jump back to start of loop

    let c = c.sel1();
    let c = c.sel2();  // send i16
    let c = c.send(-15i16);
    let c = c.zero();

    // get accumulator value
    let c = c.sel2();
    let (c, accumulator) = c.recv();
    assert_eq!(-5, accumulator);

    c.close();
}

fn main() {
    connect(srv, client_0);
    connect(srv, client_1);
}
