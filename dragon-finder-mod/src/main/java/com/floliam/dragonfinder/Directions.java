package com.floliam.dragonfinder;

import net.minecraft.util.Mth;

/** Richtungsangaben relativ zum Spieler und als Himmelsrichtung. */
final class Directions {
    private static final String[] COMPASS = {"N", "NO", "O", "SO", "S", "SW", "W", "NW"};
    private static final String[] ARROWS = {"↑", "↗", "→", "↘", "↓", "↙", "←", "↖"};

    private Directions() {
    }

    /** Minecraft-Yaw zum Ziel: 0 = Süden (+Z), 90 = Westen (-X). */
    static float yawTo(double dx, double dz) {
        return (float) Math.toDegrees(Math.atan2(-dx, dz));
    }

    static String compass(double dx, double dz) {
        float bearing = Mth.positiveModulo(yawTo(dx, dz) + 180f, 360f); // 0 = Norden, im Uhrzeigersinn
        return COMPASS[Math.round(bearing / 45f) % 8];
    }

    /** Pfeil relativ zur Blickrichtung: ↑ = geradeaus, → = rechts, ↓ = hinter dir. */
    static String arrow(double dx, double dz, float viewYaw) {
        float relative = Mth.wrapDegrees(yawTo(dx, dz) - viewYaw);
        return ARROWS[Math.round(Mth.positiveModulo(relative, 360f) / 45f) % 8];
    }

    static String height(double dy) {
        long diff = Math.round(dy);
        if (diff == 0) {
            return "gleiche Höhe";
        }
        return (diff > 0 ? "▲" : "▼") + Math.abs(diff);
    }
}
