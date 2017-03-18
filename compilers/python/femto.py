import ast
import meta
import inspect
import femto_pb2 as schema

nil = schema.Expression()
nil.nil = True

def sym(symbol):
    e = schema.Expression()
    e.symbol = symbol
    return e

def s(value):
    e = schema.Expression()
    e.string = value
    return e

def n(value):
    e = schema.Expression()
    e.number = float(value)
    return e

def l(*items):
    e = schema.Expression()
    e.list.items.extend(items)
    return e

def function(arguments, body):
    e = schema.Expression()
    e.function.arguments.extend(arguments)
    e.function.body.CopyFrom(body)
    return e

def cond(predicate, truth, falsehood):
    e = schema.Expression()
    e.condition.predicate.CopyFrom(predicate)
    e.condition.truth.CopyFrom(truth)
    e.condition.falsehood.CopyFrom(falsehood)
    return e
    
def bind(symbol, expression):
    b = schema.Binding()
    b.symbol = symbol.symbol
    b.expression.CopyFrom(expression)
    return b

def let(bindings, body):
    e = schema.Expression()
    for binding in bindings:
        b = e.let.bindings.add()
        b.CopyFrom(binding)
    e.let.body.CopyFrom(body)

    return e

def apply(operation, arguments):
    e = schema.Expression()
    e.apply.operation.CopyFrom(operation)
    e.apply.arguments.extend(arguments)
    return e

### (function [x]
###   (reduce
###    (function [a b] (+ a b))
###    0 (vals (get x "count"))))

# addTree = function(['a', 'b'],
#              apply(sym('+'), [sym('a'), sym('b')]))

# foldTree = function(['x'],
#               apply(sym('reduce'),
#                     [addTree,
#                      n(0),
#                      apply(sym('vals'),
#                            [apply(sym('get'),
#                                   [sym('x'),
#                                    s('count')])])]))

# print foldTree

def nativeSum(x):
    counts = x['count'].vals()
    return reduce(lambda a, b: a + b, 0, counts)

def tamp(z):
    return [x for y in z for x in y]
    
def astForDef(d):
    source = inspect.getsource(d)
    tree = ast.parse(source)
    return tree

def compileFemto(token):
    product = nil

    if isinstance(token, str):
        product = s(token)

    elif isinstance(token, ast.Name):
        product = sym(token.id)

    elif isinstance(token, ast.Num):
        product = n(token.n)

    elif isinstance(token, ast.Str):
        product = s(token.s)

    elif isinstance(token, ast.Add):
        product = sym('+')

    elif isinstance(token, ast.Index):
        product = compileFemto(token.value)

    elif isinstance(token, ast.Subscript):
        get = s('get')
        m = compileFemto(token.value)
        key = compileFemto(token.slice)
        product = apply(get, [m, key])

    elif isinstance(token, ast.Attribute):
        get = s('get')
        m = compileFemto(token.value)
        key = compileFemto(token.attr)
        product = apply(get, [m, key])

    elif isinstance(token, ast.Assign):
        target = compileFemto(token.targets[0])
        value = compileFemto(token.value)
        bindings = [bind(target, value)]
        product = let(bindings, nil)

    elif isinstance(token, ast.Call):
        fn = compileFemto(token.func)
        arguments = map(compileFemto, token.args)
        product = apply(fn, arguments)

    elif isinstance(token, ast.Lambda):
        arguments = map(lambda arg: compileFemto(arg).symbol, token.args.args)
        body = compileFemto(token.body)
        product = function(arguments, body)

    elif isinstance(token, ast.BinOp):
        fn = compileFemto(token.op)
        right = compileFemto(token.right)
        left = compileFemto(token.left)
        product = apply(fn, [right, left])

    elif isinstance(token, ast.Return):
        product = compileFemto(token.value)

    elif isinstance(token, ast.FunctionDef):
        arguments = map(lambda arg: compileFemto(arg).symbol, token.args.args)
        body = map(compileFemto, token.body)
        assigns = filter(lambda step: step.HasField("let"), body)
        bindings = tamp(map(lambda l: l.let.bindings, assigns))
        value = filter(lambda step: not step.HasField("let"), body)[-1]
        l = let(bindings, value)
        product = function(arguments, l)

    elif isinstance(token, ast.Module):
        product = compileFemto(token.body[0])

    else:
        print 'never seen %s type before.... compilation will be partial until this type is supported' % token.__class__

    return product

def femto(target):
    tree = astForDef(target)
    compileFemto(tree)

def run():
    print(compileFemto(astForDef(nativeSum)))

# defold = meta.decompile(nativeFold)
# source = meta.dump_python_source(defold)
