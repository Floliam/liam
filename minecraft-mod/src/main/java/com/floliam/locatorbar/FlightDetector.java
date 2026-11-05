package com.floliam.locatorbar;

import net.minecraft.ChatFormatting;
import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.PlayerInfo;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.network.chat.TextComponent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraft.world.level.GameType;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.phys.AABB;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Erkennt andere Spieler, die ohne Elytra o.ä. fliegen, und meldet das nur in deinem eigenen Chat.
 *
 * Der Server verrät dem Client nicht, ob jemand fliegt. Erkannt wird es daher an der Bewegung:
 * Wer frei in der Luft ist, muss durch die Schwerkraft immer schneller nach unten werden. Wer
 * stattdessen längere Zeit schwebt, steigt oder gleichmäßig langsam sinkt, fliegt.
 */
final class FlightDetector {
    private static final int HISTORY = 7;
    /** Bis zu dieser Sinkgeschwindigkeit (Blöcke/Tick) gilt Bewegung als schweben/fliegen statt fallen. */
    private static final double MAX_HOVER_SINK = -0.3;
    /** Echte Schwerkraft verlangsamt über 3 Ticks um mindestens ~0,1; darüber "fehlt" sie. */
    private static final double MIN_GRAVITY_ACCEL = -0.05;
    /** So viele Ticks muss jemand am Boden sein, bevor er erneut gemeldet werden kann. */
    private static final int REARM_GROUND_TICKS = 20;

    private static final Map<UUID, Track> TRACKS = new HashMap<>();

    private FlightDetector() {
    }

    static void tick(Minecraft mc) {
        if (mc.level == null || mc.player == null || !LocatorConfig.FLIGHT_ALERTS.get()) {
            TRACKS.clear();
            return;
        }
        if (mc.isPaused()) {
            return;
        }

        int alertTicks = LocatorConfig.FLIGHT_ALERT_SECONDS.get() * 20;
        Set<UUID> seen = new HashSet<>();

        for (AbstractClientPlayer other : mc.level.players()) {
            if (other == mc.player) {
                continue;
            }
            seen.add(other.getUUID());
            Track track = TRACKS.computeIfAbsent(other.getUUID(), id -> new Track());
            track.push(other.getY());

            if (!isFreelyAirborne(mc, other)) {
                track.suspicion = 0;
                if (++track.groundTicks >= REARM_GROUND_TICKS) {
                    track.alerted = false;
                }
                continue;
            }
            track.groundTicks = 0;
            if (track.count < HISTORY) {
                continue;
            }

            double recent = (track.y(0) - track.y(3)) / 3.0;
            double before = (track.y(3) - track.y(6)) / 3.0;
            boolean defiesGravity = recent > MAX_HOVER_SINK && recent - before > MIN_GRAVITY_ACCEL;
            track.suspicion = defiesGravity ? track.suspicion + 1 : Math.max(0, track.suspicion - 3);

            if (track.suspicion >= alertTicks && !track.alerted) {
                track.alerted = true;
                alert(mc, other);
            }
        }

        TRACKS.keySet().retainAll(seen);
    }

    /** true, wenn nichts den Spieler trägt und es keinen erlaubten Grund fürs In-der-Luft-Sein gibt. */
    private static boolean isFreelyAirborne(Minecraft mc, AbstractClientPlayer other) {
        if (other.isFallFlying() || other.isPassenger() || other.isAutoSpinAttack() || other.isSpectator()
                || other.isSleeping() || other.isDeadOrDying() || other.onClimbable()
                || other.isInWater() || other.isInLava()) {
            return false;
        }
        if (LocatorConfig.FLIGHT_IGNORE_CREATIVE.get() && isCreative(mc, other)) {
            return false;
        }
        if (!mc.level.hasChunkAt(other.blockPosition())) {
            return false;
        }

        AABB box = other.getBoundingBox();
        // Spinnennetz, Pulverschnee, Gerüst, Honig, Wasser usw. bremsen den Fall legal
        boolean slowingBlockNearby = mc.level.getBlockStatesIfLoaded(box.inflate(0.1)).anyMatch(state ->
                !state.getFluidState().isEmpty()
                        || state.is(Blocks.COBWEB)
                        || state.is(Blocks.POWDER_SNOW)
                        || state.is(Blocks.SCAFFOLDING)
                        || state.is(Blocks.HONEY_BLOCK)
                        || state.is(Blocks.BUBBLE_COLUMN));
        if (slowingBlockNearby) {
            return false;
        }

        // Kein Block (und kein Boot o.ä.) bis einen halben Block unter den Füßen
        return mc.level.noCollision(other, box.expandTowards(0.0, -0.5, 0.0));
    }

    private static boolean isCreative(Minecraft mc, AbstractClientPlayer other) {
        if (mc.getConnection() == null) {
            return false;
        }
        PlayerInfo info = mc.getConnection().getPlayerInfo(other.getUUID());
        return info != null && info.getGameMode() == GameType.CREATIVE;
    }

    private static void alert(Minecraft mc, AbstractClientPlayer other) {
        long distance = Math.round(other.distanceTo(mc.player));
        // displayClientMessage landet nur im eigenen Chat, es wird nichts an den Server geschickt
        mc.player.displayClientMessage(new TextComponent("[Ortungsleiste] ").withStyle(ChatFormatting.GOLD)
                .append(new TextComponent(other.getGameProfile().getName()).withStyle(ChatFormatting.YELLOW))
                .append(new TextComponent(" fliegt ohne Elytra").withStyle(ChatFormatting.RED))
                .append(new TextComponent(" (Y " + Mth.floor(other.getY()) + ", " + distance + "m)")
                        .withStyle(ChatFormatting.GRAY)), false);
        if (LocatorConfig.FLIGHT_ALERT_SOUND.get()) {
            mc.getSoundManager().play(SimpleSoundInstance.forUI(SoundEvents.NOTE_BLOCK_PLING, 1.5f));
        }
    }

    private static final class Track {
        final double[] ys = new double[HISTORY];
        int head;
        int count;
        int suspicion;
        int groundTicks;
        boolean alerted;

        void push(double y) {
            ys[head] = y;
            head = (head + 1) % HISTORY;
            count++;
        }

        /** Y-Wert von vor {@code ticksAgo} Ticks. */
        double y(int ticksAgo) {
            return ys[Math.floorMod(head - 1 - ticksAgo, HISTORY)];
        }
    }
}
