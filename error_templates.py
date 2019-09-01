def missing_perms_template(cmd, ctx, error):
    return (
        f'{ctx.message.author} failed to run {cmd}. '
        f'Missing permissions: {", ".join(error.missing_perms)}'
    )
