def parse_args_kwargs_and_as_var(parser, bits):
    """
    Parse positional, keyword and output variable arguments from a
    template tag.

    By fivethreeo
    http://djangosnippets.org/snippets/1113/

    """
    args = []
    kwargs = {}
    as_var = None
    
    bits = iter(bits)
    for bit in bits:
        if bit == 'as':
            as_var = bits.next()
            break
        else:
            for arg in bit.split(","):
                if '=' in arg:
                    k, v = arg.split('=', 1)
                    k = k.strip()
                    kwargs[k] = parser.compile_filter(v)
                elif arg:
                    args.append(parser.compile_filter(arg))
    return args, kwargs, as_var

def resolve_args_and_kwargs(args, kwargs, context):
    """
    Resolve template expressions into their values

    by fivethree0
    http://djangosnippets.org/snippets/1113/

    """
    from django.utils.encoding import smart_str

    out_args = [arg.resolve(context) for arg in args]
    out_kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                      for k, v in kwargs.items()])

    return out_args, out_kwargs
