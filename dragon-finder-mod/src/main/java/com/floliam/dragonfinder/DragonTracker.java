package com.floliam.dragonfinder;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.ClientLevel;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.LivingEntity;
import net.minecraftforge.registries.ForgeRegistries;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Sucht unter den Entities, die der Client kennt, nach Drachen und merkt sich den nächsten.
 * Der Client kennt nur Entities, die der Server in deiner Nähe überträgt (ungefähr Render-Distanz).
 */
final class DragonTracker {
    /** Erst nach so langer Zeit außer Sicht wird ein Drache erneut gemeldet (5 Minuten). */
    private static final long REALERT_TICKS = 20 * 60 * 5;

    static Sighting nearest;

    private static final Map<UUID, Long> LAST_SEEN = new HashMap<>();
    private static ClientLevel lastLevel;
    private static long ticks;
    private static Set<ResourceLocation> dragonIds = Set.of();
    private static List<? extends String> dragonIdsSource;

    private DragonTracker() {
    }

    static void tick(Minecraft mc) {
        if (mc.level != lastLevel) {
            lastLevel = mc.level;
            LAST_SEEN.clear();
            nearest = null;
            LairScanner.reset();
        }
        if (mc.level == null || mc.player == null) {
            return;
        }
        ticks++;
        LairScanner.process(mc);

        Set<ResourceLocation> ids = dragonIds();
        Sighting best = null;
        for (Entity entity : mc.level.entitiesForRendering()) {
            ResourceLocation key = ForgeRegistries.ENTITIES.getKey(entity.getType());
            if (key == null || !ids.contains(key) || !entity.isAlive()) {
                continue;
            }
            if (entity instanceof LivingEntity living && living.isDeadOrDying()) {
                continue;
            }
            double distance = entity.distanceTo(mc.player);
            Long previous = LAST_SEEN.put(entity.getUUID(), ticks);
            if (previous == null || ticks - previous > REALERT_TICKS) {
                alert(mc, entity, key);
            }
            if (best == null || distance < best.distance) {
                best = new Sighting(entity, key, distance);
            }
        }
        nearest = best;
    }

    private static Set<ResourceLocation> dragonIds() {
        List<? extends String> configured = FinderConfig.DRAGON_ENTITIES.get();
        if (configured != dragonIdsSource) {
            Set<ResourceLocation> ids = new HashSet<>();
            for (String id : configured) {
                ResourceLocation rl = ResourceLocation.tryParse(id);
                if (rl != null) {
                    ids.add(rl);
                }
            }
            dragonIds = ids;
            dragonIdsSource = configured;
        }
        return dragonIds;
    }

    private static void alert(Minecraft mc, Entity dragon, ResourceLocation key) {
        if (!FinderConfig.CHAT_ALERTS.get()) {
            return;
        }
        double dx = dragon.getX() - mc.player.getX();
        double dz = dragon.getZ() - mc.player.getZ();
        String text = " entdeckt: " + Math.round(dragon.distanceTo(mc.player)) + " m Richtung "
                + Directions.compass(dx, dz) + ", Y " + Mth.floor(dragon.getY())
                + " (" + Directions.height(dragon.getY() - mc.player.getY()) + ")";
        // Nur im eigenen Chat, es wird nichts an den Server geschickt
        mc.player.displayClientMessage(new TextComponent("[Drachenfinder] ").withStyle(ChatFormatting.GOLD)
                .append(new TextComponent(displayName(dragon, key)).withStyle(style(key)))
                .append(new TextComponent(text).withStyle(ChatFormatting.GRAY)), false);
        playSound(mc);
    }

    static void playSound(Minecraft mc) {
        if (FinderConfig.ALERT_SOUND.get()) {
            mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.NOTE_BLOCK_BELL, 1.2f));
        }
    }

    static String displayName(Entity dragon, ResourceLocation key) {
        String name = switch (key.getPath()) {
            case "fire_dragon" -> "Feuerdrache";
            case "ice_dragon" -> "Eisdrache";
            case "lightning_dragon" -> "Blitzdrache";
            default -> dragon.getType().getDescription().getString();
        };
        if (dragon.hasCustomName()) {
            name += " „" + dragon.getCustomName().getString() + "“";
        }
        return name;
    }

    static ChatFormatting style(ResourceLocation key) {
        return switch (key.getPath()) {
            case "fire_dragon" -> ChatFormatting.RED;
            case "ice_dragon" -> ChatFormatting.AQUA;
            case "lightning_dragon" -> ChatFormatting.LIGHT_PURPLE;
            default -> ChatFormatting.WHITE;
        };
    }

    static final class Sighting {
        final Entity entity;
        final ResourceLocation key;
        final double distance;

        Sighting(Entity entity, ResourceLocation key, double distance) {
            this.entity = entity;
            this.key = key;
            this.distance = distance;
        }
    }
}
