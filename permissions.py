import discord

def check_admin_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """Check if user has administrator permissions"""
    if user == guild.owner:
        return True
    
    return user.guild_permissions.administrator

def check_mod_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """Check if user has moderation permissions"""
    if user == guild.owner:
        return True
    
    perms = user.guild_permissions
    return (perms.administrator or 
            perms.kick_members or 
            perms.ban_members or 
            perms.moderate_members or
            perms.manage_messages)

def check_manage_channels_permissions(user: discord.Member, guild: discord.Guild) -> bool:
    """Check if user has manage channels permissions"""
    if user == guild.owner:
        return True
    
    perms = user.guild_permissions
    return perms.administrator or perms.manage_channels

def has_role(user: discord.Member, role_names: list) -> bool:
    """Check if user has any of the specified roles"""
    user_roles = [role.name.lower() for role in user.roles]
    return any(role.lower() in user_roles for role in role_names)
