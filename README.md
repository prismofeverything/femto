# femto

tiniest possible code serialization protocol - transmit the AST directly

![FEMTO](https://github.com/prismofeverything/femto/blob/master/femto.jpg)

## idea

The idea is that while we are serializing everything else, our functions still remain puzzlingly opaque once assembled. This is largely because functions are so context dependent. Every component of a function definition is basically a reference to some other function or value defined elsewhere. That makes them slippery entities to define. Do you `uberjar` a function, package the world so to speak and carry along the context of the function with it? This is the illusion our closures perpetuate, but that is while running inside our system. Transmitting a closure across the wire is still something we don't really do much, but would be a very interesting next step!

We are not transmitting closures here. In fact, nothing about the lexical environment is encoded. It is environment agnostic, in that you can provide whatever environment you wish and as long as all symbolic references are fulfilled the function applies.

So, **femto** specifies a schema (in protobuffer) that can be used to express any program. At least, the structure of it. I mean, I'm pretty sure. I haven't proven it but it seems like a reasonable assumption.

The schema aims to be as minimal as possible. As it is, an `Expression` message can be one of:

* nil
* symbol
* string
* number
* list
* condition
* function
* let
* apply

Some immediate things missing that come to mind:

* maps
* integer/double duality at least
* loops

That said, it is fairly effective. The following snippet of python:

    def nativeSum(x):
        counts = x['count'].vals()
        return reduce(lambda a, b: a + b, 0, counts)

is converted into the following protobuf encoded data:

    femto(nativeSum)

    ----->
    function {
      arguments: "x"
      body {
        let {
          bindings {
            symbol: "counts"
            expression {
              apply {
                operation {
                  apply {
                    operation {
                      string: "get"
                    }
                    arguments {
                      apply {
                        operation {
                          string: "get"
                        }
                        arguments {
                          symbol: "x"
                        }
                        arguments {
                          string: "count"
                        }
                      }
                    }
                    arguments {
                      string: "vals"
                    }
                  }
                }
              }
            }
          }
          body {
            apply {
              operation {
                symbol: "reduce"
              }
              arguments {
                function {
                  arguments: "a"
                  arguments: "b"
                  body {
                    apply {
                      operation {
                        symbol: "+"
                      }
                      arguments {
                        symbol: "b"
                      }
                      arguments {
                        symbol: "a"
                      }
                    }
                  }
                }
              }
              arguments {
                number: 0.0
              }
              arguments {
                symbol: "counts"
              }
            }
          }
        }
      }
    }
    
Seems laborious, but... our code is data! Now we can transform or materialize it however we wish.

## future

The first conversion existing is from python to femto. JS to femto is next. Then being able to interpret a femto expression given a context map would be really cool. Then you could serialize a python function and run it in JS, or vice versa.

Is this crazy?? I'm not sure. Kind of fun though.