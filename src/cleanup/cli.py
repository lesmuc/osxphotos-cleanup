import click

from cleanup.scanner import scan_library, get_library_summary
from cleanup.rules import run_all_rules
from cleanup.agent import analyze_photo
from cleanup.albums import organize_into_albums
from cleanup.models import SuggestedAction

@click.command()
@click.option("--limit", default=0, help="Maximale Fotos zum Scannen (0=alle)")
@click.option("--dry-run", is_flag=True, help="Nur Vorschläge zeigen, keine Alben erstellen")
@click.option("--no-ai", is_flag=True, help="Ollama Vision für REVIEW-Fotos überspringen")
def main(limit, dry_run, no_ai):
    """Scannt die Photos Library und schlägt Aufräum-Aktionen vor."""

    # 1. Scannen
    click.echo("Scanne Photos Library...")
    photos = scan_library(limit=limit)
    summary = get_library_summary(photos)
    click.echo(f"  {summary.total_photos} Fotos, {summary.total_videos} Videos")
    click.echo(f"  {summary.total_size_gb:.1f} GB, {summary.screenshots} Screenshots, {summary.bursts} Bursts")

    # 2. Rules
    click.echo("\nWende Regeln an...")
    suggestions = run_all_rules(photos)
    click.echo(f"  {len(suggestions)} Aufräum-Kandidaten gefunden")

    # 3. AI (optional)
    if not no_ai:
        review_photos = []
        for s in suggestions:
            if s.action == SuggestedAction.REVIEW:
                review_photos.append(s)
        if review_photos:
            click.echo(f"\nAnalysiere {len(review_photos)} Fotos mit Ollama Vision...")
            for s in review_photos:
                photo = None
                for p in photos:
                    if p.metadata.uuid == s.photo_uuid:
                        photo = p
                        break

                if photo and photo.metadata.path:
                    if photo.metadata.is_movie:                                                                                                                                    
                        continue

                    click.echo(f"  Analysiere: {photo.metadata.original_filename} ({photo.metadata.filename})")                    
                    analysis = analyze_photo(photo, s.reason, on_status=click.echo)
                    s.action = analysis.suggestedAction
                    s.reason = f"AI: {analysis.reason}"
                    s.confidence = analysis.confidence
                    click.echo(f"  {photo.metadata.original_filename}: {analysis.suggestedAction.value} — {analysis.reason}")

    # 4. Zusammenfassung
    click.echo("\n--- Zusammenfassung ---")
    for action in SuggestedAction:
        count = 0
        for s in suggestions:
            if s.action == action:
                count += 1
        if count > 0:
            click.echo(f"  {action.value}: {count}")

    # 5. Alben erstellen
    if not dry_run and suggestions:
        click.echo("\nErstelle Alben in Photos.app...")
        organize_into_albums(suggestions)
        click.echo("Fertig! Öffne Photos.app um die Alben zu prüfen.")
    elif dry_run:
        click.echo("\n(Dry-Run — keine Alben erstellt)")

