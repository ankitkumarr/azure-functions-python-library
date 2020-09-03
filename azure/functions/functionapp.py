import inspect

class AzureFunctionApp(object):

    def __init__(self, app_name):
        # dictionary of functions: 
        # - key : string : name of function
        # - value : AzureFunction : function to run
        self.functions = {}
        self.app_name = app_name

    def trigger(self, trigger):
        def decorator(function):
            # make sure that the function is actually an azure function
            if not isinstance(function, AzureFunction):
                function = AzureFunction(function)
            function.bindings.append(trigger)
            self.add_function(function)
            return function
        return decorator


    def input(self, input):
        def decorator(function):
            if not isinstance(function, AzureFunction):
                function = AzureFunction(function)
            function.bindings.append(input)
            return function
        return decorator

    def output(self, output):
        def decorator(function):
            # make sure that the function is actually an azure function
            if not isinstance(function, AzureFunction):
                function = AzureFunction(function)
            function.bindings.append(output)
            return function
        return decorator

    def add_function(self, function):
        self.functions[function.name] = function
        functionArgs = list(function.function.__code__.co_varnames)
        functionArgs = functionArgs[0:function.function.__code__.co_argcount]
        #need to go back and figure out what the bindings names are for their args
        for binding in function.bindings:
            if binding.name != '$return':
                binding.name = functionArgs.pop()

    def register_blueprint(self, blueprint):
        for key, value in blueprint.functions.items():
            self.functions[key] = value

    def HttpTrigger(self,  argName=None, route=None, authLevel="anonymous", methods=["get", "post"]):
        trigger = HttpTrigger(argName, route, authLevel, methods)

        def decorator(function):
            # make sure that the function is actually an azure function
            if not isinstance(function, AzureFunction):
                function = AzureFunction(function)
            function.bindings.append(trigger)
            self.add_function(function)
            return function
        return decorator

    def HttpOutput(self):
        output = Http()

        def decorator(function):
            # make sure that the function is actually an azure function
            if not isinstance(function, AzureFunction):
                function = AzureFunction(function)
            function.bindings.append(output)
            return function
        return decorator


class AzureFunction(object):

    def __init__(self, function):
        self.name = function.__name__
        ###### Do we even need these ######
        self.script_file = ""
        self.function_directory = ""
        self.entry_point = function.__name__
        self.language = "python"
        ###################################
        self.function = function
        self.bindings = []

class Binding(object):

    def __init__(self, binding_type, connection, name, cardinality, direction, data_type):
        self.type = binding_type
        self.connection = connection
        self.name = name
        self.cardinality = cardinality
        self.direction = direction
        self.data_type = data_type


class HttpTrigger(Binding):
    def __init__(self, argName=None, route=None, authLevel="anonymous", methods=["get", "post"]):
        super().__init__('httpTrigger', None, argName, None, 'in', None)
        self.route = route
        self.authLevel = authLevel
        self.methods = methods

class Http(Binding):
    def __init__(self):
        super().__init__('http', None, '$return', None, 'out', None)

# TODO: Fix this
class BlobInput(Binding):
    def __init__(self, path, connection):
        super().__init__('blob', 'connection', 'this gon be the function param', 'cardinality', 'in', 'binary')
        self.path = path
        self.connection = connection

class Blueprint(AzureFunctionApp):
    def __init__(self, app_name):
        super().__init__(app_name)
    