function isFunction(f) {
  return !!(f && f.constructor && f.call && f.apply);
}

function isNumber(n) {
  return !isNaN(n) && typeof(n) === 'number'
}

var _bind = Function.prototype.apply.bind(Function.prototype.bind);
Object.defineProperty(Function.prototype, 'bind', {
  value: function(obj) {
    var boundFunction = _bind(this, arguments);
    boundFunction.boundObject = obj;
    return boundFunction;
  }
});

femto = function() {
  function lookup(env, key) {
    if (env.length > 0) {
      var keys = Object.keys(env[0])
      if (keys.indexOf(key) > -1) {
        var found = env[0][key]
        return found
      } else {
        return lookup(env.slice(1), key)
      }
    } else {
      console.log('unbound symbol! ' + key)
    }
  }

  function evaluate(env, femto) {
    var key = Object.keys(femto)[0]
    console.log(key)
    if (key === 'nil') {
      value = null
    } else if (key === 'string' || key === 'number') {
      value = femto[key]
    } else if (key === 'symbol') {
      var value = lookup(env, femto[key])
    } else if (key === 'list') {
      value = femto['list']['items'].map(function(sub) {return evaluate(env, sub)})
    } else if (key === 'condition') {
      var condition = femto['condition']
      var predicate = evaluate(env, condition['predicate'])
      if (predicate === null || predicate == false || predicate == undefined) {
        value = evaluate(env, condition['falsehood'])
      } else {
        value = evaluate(env, condition['truth'])
      }
    } else if (key === 'function') {
      var fn = femto['function']
      var args = fn['arguments']
      var body = fn['body']
      var program = function() {
        var bindings = Array.prototype.slice.call(arguments);
        var scope = args.reduce(function(scope, symbol, index) {
          var found = bindings[index]
          scope[symbol] = found
          return scope
        }, {})
        var newenv = [scope].concat(env)
        var value = evaluate(newenv, body)
        return value
      }
      value = program
    } else if (key === 'let') {
      var assign = femto['let']
      var scope = assign['bindings'].reduce(function(scope, binding) {
        var key = binding['symbol']
        var value = evaluate(env, binding['expression'])
        scope[key] = value
        return scope
      }, {})
      var newenv = [scope].concat(env)
      var value = evaluate(newenv, assign['body'])
      value = value
    } else if (key === 'apply') {
      var apply = femto['apply']
      var op = evaluate(env, apply['operation'])
      var args = apply['arguments'] ? apply['arguments'].map(function(sub) {return evaluate(env, sub)}) : []
      var result = op.apply(op.boundObject, args)
      value = result
    } else {
      console.log('unknown syntax! ' + JSON.stringify(femto))
      value = undefined
    }

    console.log(value)
    return value
  }

  return evaluate
} ();

python = { "function": { "body": { "let": { "body": { "apply": { "operation": { "symbol": "reduce" }, "arguments": [ { "function": { "body": { "apply": { "operation": { "symbol": "+" }, "arguments": [ { "symbol": "b" }, { "symbol": "a" } ] } }, "arguments": [ "a", "b" ] } }, { "number": 0.0 }, { "symbol": "counts" } ] } }, "bindings": [ { "symbol": "counts", "expression": { "apply": { "operation": { "apply": { "operation": { "symbol": "attribute" }, "arguments": [ { "apply": { "operation": { "symbol": "get" }, "arguments": [ { "symbol": "x" }, { "string": "count" } ] } }, { "string": "vals" } ] } } } } } ] } }, "arguments": [ "x" ] }}

environment = [{
  '+': function(a, b) {
    if (isNumber(a)) {
      if (isNumber(b)) {
        return a + b
      } else {
        return a
      }
    } else {
      return isNumber(b) ? b : 0
    }
  },

  'reduce': function(f, i, l) {return l.reduce(f, i)},
  'get': function(m, k) {return m[k]},
  'attribute': function(m, k) {
    var value = m[k]
    if (isFunction(value)) {
      var fn = value.bind(m)
    }
    return fn
  }
}]

var py = femto(environment, python)
var result = py({count: {a: 1, b: 2, c: 3, d: 4, e: 5, f: 6, vals: function(m) {return Object.values(m || this)}}})
console.log(result)
