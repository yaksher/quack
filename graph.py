import matplotlib.pyplot as plt
from sympy.parsing.sympy_parser import parse_expr
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application
from sympy import *
import numpy as np

from quack_common import *

description = ""

bot = commands.Bot(command_prefix='?', description=description)

transformations = (standard_transformations + (implicit_multiplication_application,))

@bot.event
async def on_ready():
    exec(ready)

@bot.command()
async def restart(ctx, *args):
    if "graphbot".startswith(" ".join(args)):
        restart_func(ctx.author.id)

@bot.command()
async def graph(ctx, *args):#x_bound:str, y_bound = "", *args):
    in_str = " ".join(args).strip("`")
    bound_y = r"y ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    bound_x = r"x ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    y_bound = re.findall(bound_y, in_str)
    x_bound = re.findall(bound_x, in_str)
    if y_bound:
        in_str = re.sub(bound_y, lambda y: "", in_str)
        y_bounds = tuple(float(y) for y in y_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        y_bounds = None
    if x_bound:
        in_str = re.sub(bound_x, lambda x: "", in_str)
        x_bounds = tuple(float(x) for x in x_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        x_bounds = (-1, 1)
    expr = sympify(in_str.strip(", "))
    expr.subs(Symbol("e"), np.e)
    expr.subs(Symbol("pi"), np.pi)
    expr.subs(Symbol("π"), np.pi)
    try:
        f = lambdify(Symbol("x"), expr, modules=numpy)
        x = np.linspace(*x_bounds, 400)
    except:
        f = np.vectorize(lambda x: expr.subs(Symbol("x"), x))
        x = np.linspace(*x_bounds, 100)
    y = f(x)
    for i, y_elem in enumerate(y):
        try:
            y[i] = float(y[i])
        except:
            y[i] = np.NaN
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.set(xlim=x_bounds)
    ax.spines['top'].set_visible(False)#.set_color('white') 
    ax.spines['right'].set_visible(False)#.set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.grid(True)
    #ax.axis("equal")
    if y_bounds is not None:
        ax.set(ylim=y_bounds)
    ax.plot(x, y)
    ax.spines['left'].set_position(('data', min(max(ax.get_xlim()[0], 0), ax.get_xlim()[1])))
    ax.spines['bottom'].set_position(('data', min(max(ax.get_ylim()[0], 0), ax.get_ylim()[1])))
    buf = io.BytesIO()
    buf.name = "graph.png"
    fig.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    await ctx.send(file=discord.File(buf))

@bot.command()
async def graph_param(ctx):#, *args):#x_bound:str, y_bound = "", *args):
    in_str = ctx.message.content[len("?graph_param"):].strip("` ")
    polar = in_str.startswith("polar")
    in_str = in_str[5:] if polar else in_str
    bound_y = r"y ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    bound_x = r"x ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    bound_t = r"t ?= ?\(-?[0-9]+\.?[0-9]*, ?-?[0-9]+\.?[0-9]*\)"
    y_bound = re.findall(bound_y, in_str)
    x_bound = re.findall(bound_x, in_str)
    t_bound = re.findall(bound_t, in_str)
    if y_bound:
        in_str = re.sub(bound_y, lambda y: "", in_str)
        y_bounds = tuple(float(y) for y in y_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        y_bounds = None
    if x_bound:
        in_str = re.sub(bound_x, lambda x: "", in_str)
        x_bounds = tuple(float(x) for x in x_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        x_bounds = None
    if t_bound:
        in_str = re.sub(bound_t, lambda t: "", in_str)
        t_bounds = tuple(float(t) for t in t_bound[0].replace(" ", "")[3:-1].split(","))
    else:
        t_bounds = (0,1)
    expr_x, expr_y = [sympify(s.strip(", ")) for s in in_str.split("|")]
    expr_x.subs(Symbol("e"), np.e)
    expr_x.subs(Symbol("pi"), np.pi)
    expr_x.subs(Symbol("π"), np.pi)
    expr_y.subs(Symbol("e"), np.e)
    expr_y.subs(Symbol("pi"), np.pi)
    expr_y.subs(Symbol("π"), np.pi)
    try:
        fx = lambdify(Symbol("t"), expr_x, modules=numpy)
        fy = lambdify(Symbol("t"), expr_y, modules=numpy)
        t = np.linspace(*t_bounds, 400)
    except:
        fx = np.vectorize(lambda t: expr_x.subs(Symbol("t"), t))
        fy = np.vectorize(lambda t: expr_y.subs(Symbol("t"), t))
        t = np.linspace(*t_bounds, 100)
    x = fx(t)
    y = fy(t)
    for i in range(len(t)):
        try:
            x[i] = float(x[i])
        except:
            x[i] = np.NaN
        try:
            y[i] = float(y[i])
        except:
            y[i] = np.NaN
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, polar=polar)
    if not polar:
        ax.spines['top'].set_visible(False)#.set_color('white') 
        ax.spines['right'].set_visible(False)#.set_color('white')
        ax.spines['left'].set_color('white')
        ax.spines['bottom'].set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True)
        #ax.axis("equal")
        if x_bounds is not None:
            ax.set(xlim=x_bounds)
        if y_bounds is not None:
            ax.set(ylim=y_bounds)
        ax.spines['left'].set_position(('data', min(max(ax.get_xlim()[0], 0), ax.get_xlim()[1])))
        ax.spines['bottom'].set_position(('data', min(max(ax.get_ylim()[0], 0), ax.get_ylim()[1])))
    else:
        for spine in ax.spines.values():
            spine.set_color('white')
            ax.tick_params(colors='white')
            label_positions = ax.get_xticks()
            xL=['0',r'$\frac{\pi}{4}$',r'$\frac{\pi}{2}$',r'$\frac{3\pi}{4}$',\
                r'$\pi$',r'$\frac{5\pi}{4}$',r'$\frac{3\pi}{2}$',r'$\frac{7\pi}{4}$']
            ax.set_xticklabels(xL)
    ax.plot(x, y)
    buf = io.BytesIO()
    buf.name = "graph.png"
    fig.savefig(buf, format='png', transparent=True)
    buf.seek(0)
    await ctx.send(file=discord.File(buf))

bot.run(token)
