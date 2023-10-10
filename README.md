# GitBundle

This is a template repository for GitBundle Premium Edition.

For production environment, user should configure the ssl cert. Like using `acme.sh` for auto configure ssl.

For local environment, use `mkcert` to generate the ssl cert, and then run `hack.sh` before starting container.

## Notes

The required database may need to create first

# Use your own env
```bash
cp env-example .env
```