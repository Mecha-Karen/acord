
# Welcome to ACords getting started guide!
import acord
import types
from typing import Callable
import asyncio
commander = Callable[...,types.FunctionType]
# Define your client!





    



class Commander:

  
  
    
  def __init__(self,**kwargs):
    self.prefix = kwargs["prefix"]
    del kwargs["prefix"]
    
    bot = acord.Client(**kwargs)
    self.bot = bot
    
    self.cmds = {}
    self.current = []
  
  @property
  def commands(self):
    return self.cmds

  def command(self,name=None,aliases=[],description="",) -> Callable[[commander],commander]:
    self.current = [name,aliases,description]
    

    def _command(cmd:commander) -> commander:
      name = self.current[0]
      aliases = self.current[1]
      desc = self.current[2]
      if name == None:
        name = cmd.__name__
      
      
      
      args = cmd.__code__.co_varnames
      argsr = []
      
      
      for arg in args:
        argsr.append(arg)
      args = argsr
      self.cmds[name] = {}
      self.cmds[name]["func"] = cmd
      self.cmds[name]["args"] = args
      self.cmds[name]["aliases"] = aliases
      self.cmds[name]["description"] = desc
      self.current = []
      
      
      return cmd
    
    return _command
  def run(self,**kwargs):
    @self.bot.on("message_create")
    async def on_message_create(message: acord.Message):
      
      # Listen to all message, if content == ".ping"
      if message.content.startswith(self.prefix):
        # Return "Pong!"
        q = message.content.split(" ")
        cmd = q[0].replace(self.prefix,"")
        args = q[1:]
        cd = None
        def get_cmd(cmd,cmds):
          for cm in cmds:
            if cmd == cm or self.cmd in cmds[cm]["aliases"]:
              return cmds[cm]
            else:
              return None
        cd = get_cmd(cmd,self.cmds)
        if cd == None:
          return
        k = {}
        k["ctx"] = message
        
        ar = cd["args"]
        c = 0
        try:
          for arg in ar:
            if arg.startswith("*"):
              k[arg] = args[c:]
            else:
              
              k[arg] = args[c]
            c += 1
        except IndexError:
          ok = ""
        
        f = cd["func"]

        try:
          await f(**k)
        except Exception as e:
          print(f"ERROR -> {cmd} @\n`{e}`")
    try:
      self.bot.run(**kwargs)
    except Exception as e:
      print(f"ERROR -> Bot.run @\n`{e}`")



