package com.floliam.locatorbar;

import net.minecraftforge.common.ForgeConfigSpec;

/** Einstellungen in config/playerlocatorbar-client.toml */
public final class LocatorConfig {
    public static final ForgeConfigSpec SPEC;

    public static final ForgeConfigSpec.BooleanValue ENABLED;
    public static final ForgeConfigSpec.IntValue FIELD_OF_VIEW;
    public static final ForgeConfigSpec.IntValue MAX_DISTANCE;
    public static final ForgeConfigSpec.BooleanValue SHOW_OUT_OF_VIEW;
    public static final ForgeConfigSpec.BooleanValue SHOW_HEIGHT;
    public static final ForgeConfigSpec.BooleanValue SHOW_DISTANCE;
    public static final ForgeConfigSpec.BooleanValue SHOW_NAME;
    public static final ForgeConfigSpec.BooleanValue SHOW_INVISIBLE;

    public static final ForgeConfigSpec.BooleanValue FLIGHT_ALERTS;
    public static final ForgeConfigSpec.IntValue FLIGHT_ALERT_SECONDS;
    public static final ForgeConfigSpec.BooleanValue FLIGHT_IGNORE_CREATIVE;
    public static final ForgeConfigSpec.BooleanValue FLIGHT_ALERT_SOUND;

    static {
        ForgeConfigSpec.Builder b = new ForgeConfigSpec.Builder();
        b.push("bar");

        ENABLED = b.comment("Leiste beim Spielstart anzeigen (im Spiel mit der Taste J umschaltbar)")
                .define("enabled", true);
        FIELD_OF_VIEW = b.comment("Wie viele Grad die Leiste von links nach rechts abdeckt (360 = Rundum-Kompass)")
                .defineInRange("fieldOfView", 120, 30, 360);
        MAX_DISTANCE = b.comment("Spieler weiter weg als so viele Blöcke ausblenden (0 = keine Grenze)")
                .defineInRange("maxDistance", 0, 0, 100000);
        SHOW_OUT_OF_VIEW = b.comment("Spieler außerhalb des Blickfelds halbtransparent am Rand der Leiste zeigen")
                .define("showOutOfView", true);
        SHOW_HEIGHT = b.comment("Höhe (Y) des nächsten Spielers rechts neben der Leiste anzeigen")
                .define("showHeight", true);
        SHOW_DISTANCE = b.comment("Entfernung zum nächsten Spieler links neben der Leiste anzeigen")
                .define("showDistance", true);
        SHOW_NAME = b.comment("Namen des nächsten Spielers links neben der Leiste anzeigen")
                .define("showName", false);
        SHOW_INVISIBLE = b.comment("Auch Spieler mit Unsichtbarkeitstrank anzeigen")
                .define("showInvisible", true);

        b.pop();
        b.push("flightAlert");

        FLIGHT_ALERTS = b.comment("Im eigenen Chat melden, wenn ein Spieler ohne Elytra o.ä. fliegt")
                .define("enabled", true);
        FLIGHT_ALERT_SECONDS = b.comment("So viele Sekunden muss jemand frei in der Luft schweben/steigen, bevor gemeldet wird")
                .defineInRange("seconds", 3, 1, 30);
        FLIGHT_IGNORE_CREATIVE = b.comment("Spieler im Kreativmodus nicht melden (dort ist Fliegen normal)")
                .define("ignoreCreative", true);
        FLIGHT_ALERT_SOUND = b.comment("Bei einer Meldung einen kurzen Ton abspielen (nur für dich hörbar)")
                .define("sound", true);

        b.pop();
        SPEC = b.build();
    }

    private LocatorConfig() {
    }
}
