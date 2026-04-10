import click
from tabulate import tabulate
from app.integrations.openrouter_client import OpenRouterClient


@click.group()
def cli():
    """OpenRouter Free Models Navigator - Terminal-based AI Model Selection"""
    pass


@cli.command()
def list_models():
    """📊 List all available free OpenRouter models"""
    client = OpenRouterClient()
    models = client.list_free_models()
    
    if not models:
        click.echo(click.style("❌ No models found. Check your API key configuration.", fg="red"))
        return
    
    table_data = [
        [
            click.style(m["id"], fg="cyan"),
            m.get("context_length", "N/A"),
            click.style("FREE ✓", fg="green") if m.get("pricing", {}).get("prompt") == "0" else "PAID"
        ]
        for m in models
    ]
    
    click.echo("\n")
    click.echo(click.style("📊 Available Free AI Models on OpenRouter:\n", fg="yellow", bold=True))
    click.echo(tabulate(
        table_data,
        headers=[click.style("Model ID", bold=True), click.style("Context Length", bold=True), click.style("Cost", bold=True)],
        tablefmt="grid"
    ))
    click.echo(f"\n✅ Total Models Available: {len(models)}\n")


@cli.command()
@click.option('--model', prompt='Select model ID', help='OpenRouter model ID', type=str)
@click.option('--message', prompt='Enter your message', help='Message to send', type=str)
def chat(model: str, message: str):
    """💬 Chat with a selected model"""
    client = OpenRouterClient()
    
    # Validate model
    if not client.validate_model(model):
        click.echo(click.style(f"❌ Model '{model}' not found in available free models.", fg="red"))
        click.echo("Use 'list-models' command to see available models.")
        return
    
    click.echo(f"\n{click.style('🤖 Using model:', fg='cyan')} {click.style(model, fg='yellow')}\n")
    click.echo(click.style("Response:\n", fg='green'))
    
    try:
        for chunk in client.stream_response(model, [{"role": "user", "content": message}]):
            click.echo(chunk, nl=False)
        click.echo("\n")
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))


@cli.command()
def interactive():
    """🎯 Interactive terminal navigation through models"""
    client = OpenRouterClient()
    models = client.list_free_models()
    
    if not models:
        click.echo(click.style("❌ No models found. Check your API key configuration.", fg="red"))
        return
    
    click.echo("\n")
    click.echo(click.style("🎯 Interactive Model Navigator\n", fg="yellow", bold=True))
    
    for idx, model in enumerate(models, 1):
        click.echo(f"{click.style(str(idx), fg='cyan', bold=True)}. {click.style(model['id'], fg='green')}")
    
    try:
        choice = click.prompt(
            click.style("\nSelect model (number)", fg='cyan'),
            type=click.IntRange(1, len(models))
        )
        selected_model = models[choice - 1]["id"]
    except (ValueError, IndexError):
        click.echo(click.style("❌ Invalid selection", fg="red"))
        return
    
    click.echo(f"\n✅ Selected: {click.style(selected_model, fg='green', bold=True)}")
    click.echo(click.style("Start chatting (type 'exit' to quit):\n", fg='yellow'))
    
    while True:
        try:
            user_input = click.prompt(click.style("You", fg='cyan'))
            if user_input.lower() == 'exit':
                click.echo(click.style("\n👋 Goodbye!", fg='yellow'))
                break
            
            response = client.generate_response(
                selected_model,
                [{"role": "user", "content": user_input}]
            )
            click.echo(f"{click.style('Bot', fg='green')}: {response}\n")
        except KeyboardInterrupt:
            click.echo(click.style("\n\n👋 Goodbye!", fg='yellow'))
            break
        except Exception as e:
            click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))


@cli.command()
@click.option('--model', prompt='Select model ID', help='OpenRouter model ID', type=str)
def model_info(model: str):
    """ℹ️ Get detailed information about a specific model"""
    client = OpenRouterClient()
    info = client.get_model_info(model)
    
    if not info:
        click.echo(click.style(f"❌ Model '{model}' not found.", fg="red"))
        return
    
    click.echo("\n")
    click.echo(click.style(f"📋 Model Information: {info['id']}\n", fg="yellow", bold=True))
    click.echo(f"Name: {click.style(info['name'], fg='cyan')}")
    click.echo(f"Context Length: {click.style(str(info['context_length']), fg='green')}")
    click.echo(f"Description: {info['description']}")
    pricing = info.get('pricing', {})
    click.echo(f"Pricing - Prompt: {click.style(str(pricing.get('prompt', 'N/A')), fg='green')}")
    click.echo(f"Pricing - Completion: {click.style(str(pricing.get('completion', 'N/A')), fg='green')}")
    click.echo()


if __name__ == '__main__':
    cli()