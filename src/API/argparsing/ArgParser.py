import argparse
import inspect
from datetime import datetime

class ArgParser:
    def __init__(self, controller):
        self.parser = argparse.ArgumentParser(description="CLI Interface")
        subparsers = self.parser.add_subparsers(dest="command", required=True)
        self.handlers = {}

        for name, method in inspect.getmembers(controller, inspect.ismethod):
            if name.startswith("__"):
                continue
                
            help_msg = method.__doc__.split("\n")[0] if method.__doc__ else name
            cmd_parser = subparsers.add_parser(name, help=help_msg)
            
            sig = inspect.signature(method)
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                    
                kwargs = {}
                
                if param.annotation == bool:
                    kwargs["action"] = "store_true"
                elif param.annotation == list:
                    kwargs["nargs"] = "*"
                elif param.annotation == int:
                    kwargs["type"] = int
                elif param.annotation == datetime:
                    kwargs["type"] = str
                else:
                    kwargs["type"] = str
                
                if param.default is not param.empty:
                    kwargs["default"] = param.default
                    kwargs["required"] = False
                else:
                    kwargs["required"] = True
                
                cmd_parser.add_argument(f"--{param_name}", **kwargs)
            
            self.handlers[name] = method

    async def execute(self):
        args = self.parser.parse_args()
        if not args.command:
            self.parser.print_help()
            return

        method = self.handlers[args.command]
        kwargs = {}
        
        for param_name, param in inspect.signature(method).parameters.items():
            if param_name == "self":
                continue
                
            value = getattr(args, param_name)
            
            if param.annotation == datetime and value is not None:
                formats = ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
                for fmt in formats:
                    try:
                        value = datetime.strptime(value, fmt)
                        break
                    except ValueError:
                        pass
                else:
                    raise ValueError(f"Invalid datetime format: {value}")
            
            elif param.annotation == list and value is not None:
                if isinstance(value, str):
                    value = [item.strip() for item in value.split(",")]
                elif not isinstance(value, list):
                    value = [value]
            
            kwargs[param_name] = value
        
        await method(**kwargs)