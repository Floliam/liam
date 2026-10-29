package com.floliam.locatorbar;

import com.mojang.blaze3d.vertex.PoseStack;
import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiComponent;
import net.minecraft.client.player.AbstractClientPlayer;
import net.minecraft.client.player.LocalPlayer;
import net.minecraft.util.Mth;
import net.minecraftforge.client.gui.ForgeIngameGui;
import net.minecraftforge.client.gui.IIngameOverlay;

import java.util.ArrayList;
import java.util.List;

/**
 * Zeichnet eine Leiste über der XP-Leiste. Jeder andere Spieler ist ein Punkt; die
 * horizontale Lage entspricht der Richtung relativ zu deiner Blickrichtung (Mitte = geradeaus).
 * Der nächste Spieler ist größer und bekommt Entfernung und Höhe als Text daneben.
 */
public class LocatorBarOverlay implements IIngameOverlay {
    private static final int BAR_WIDTH = 182;
    private static final int HALF_WIDTH = BAR_WIDTH / 2;
    /** So viele Pixel rücken Herzen, Rüstung und Hunger nach oben, um Platz für die Leiste zu machen. */
    private static final int RESERVED_HEIGHT = 12;
    /** Abstand der Leistenmitte vom unteren Bildschirmrand (zwischen XP-Zahl und Herzen). */
    private static final int BAR_CENTER_FROM_BOTTOM = 39;

    private static final int LINE_COLOR = 0x99FFFFFF;
    private static final int LINE_SHADOW = 0x66000000;
    private static final int CENTER_TICK = 0xFFFFFFFF;
    private static final int OUTLINE = 0xFF000000;
    private static final int UP_COLOR = 0x55FF55;
    private static final int DOWN_COLOR = 0xFF5555;
    private static final int TEXT_COLOR = 0xFFFFFF;

    @Override
    public void render(ForgeIngameGui gui, PoseStack poseStack, float partialTick, int width, int height) {
        Minecraft mc = Minecraft.getInstance();
        LocalPlayer self = mc.player;
        if (self == null || mc.level == null || mc.options.hideGui || !ClientSetup.isVisible()) {
            return;
        }

        gui.left_height += RESERVED_HEIGHT;
        gui.right_height += RESERVED_HEIGHT;

        int left = width / 2 - HALF_WIDTH;
        int centerX = width / 2;
        int cy = height - BAR_CENTER_FROM_BOTTOM;

        // Linie mit kleiner Markierung für "geradeaus"
        GuiComponent.fill(poseStack, left, cy - 1, left + BAR_WIDTH, cy + 2, LINE_SHADOW);
        GuiComponent.fill(poseStack, left, cy, left + BAR_WIDTH, cy + 1, LINE_COLOR);
        GuiComponent.fill(poseStack, centerX, cy - 2, centerX + 1, cy + 3, CENTER_TICK);

        double px = Mth.lerp(partialTick, self.xo, self.getX());
        double py = Mth.lerp(partialTick, self.yo, self.getY());
        double pz = Mth.lerp(partialTick, self.zo, self.getZ());
        float viewYaw = self.getViewYRot(partialTick);

        double halfFov = LocatorConfig.FIELD_OF_VIEW.get() / 2.0;
        int maxDistance = LocatorConfig.MAX_DISTANCE.get();
        boolean showOutOfView = LocatorConfig.SHOW_OUT_OF_VIEW.get();
        boolean hideInvisible = LocatorConfig.HIDE_INVISIBLE.get();

        List<Marker> markers = new ArrayList<>();
        Marker closest = null;

        for (AbstractClientPlayer other : mc.level.players()) {
            if (other == self || (other.isSpectator() && !self.isSpectator())) {
                continue;
            }
            if (hideInvisible && other.isInvisibleTo(self)) {
                continue;
            }

            double ox = Mth.lerp(partialTick, other.xo, other.getX());
            double oy = Mth.lerp(partialTick, other.yo, other.getY());
            double oz = Mth.lerp(partialTick, other.zo, other.getZ());
            double dx = ox - px;
            double dy = oy - py;
            double dz = oz - pz;
            double distance = Math.sqrt(dx * dx + dy * dy + dz * dz);
            if (maxDistance > 0 && distance > maxDistance) {
                continue;
            }

            // Minecraft-Yaw: 0 = Süden (+Z), 90 = Westen (-X); größerer Winkel = weiter rechts
            float targetYaw = (float) Math.toDegrees(Math.atan2(-dx, dz));
            float delta = Mth.wrapDegrees(targetYaw - viewYaw);
            boolean inView = Math.abs(delta) <= halfFov;
            if (!inView && !showOutOfView) {
                continue;
            }

            double offset = Mth.clamp(delta / halfFov, -1.0, 1.0);
            int x = centerX + (int) Math.round(offset * (HALF_WIDTH - 3));

            Marker marker = new Marker(other, x, distance, oy, dy, inView);
            markers.add(marker);
            if (closest == null || distance < closest.distance) {
                closest = marker;
            }
        }

        for (Marker marker : markers) {
            if (marker != closest) {
                drawDot(poseStack, marker, cy, 1);
            }
        }
        if (closest == null) {
            return;
        }
        drawDot(poseStack, closest, cy, 2);
        drawLabels(mc.font, poseStack, closest, left, cy);
    }

    private static void drawDot(PoseStack poseStack, Marker marker, int cy, int radius) {
        int alpha = marker.inView ? 0xFF : 0x70;
        int outline = (OUTLINE & 0x00FFFFFF) | (alpha << 24);
        int color = colorFor(marker.player) | (alpha << 24);
        int x = marker.x;
        GuiComponent.fill(poseStack, x - radius - 1, cy - radius - 1, x + radius + 2, cy + radius + 2, outline);
        GuiComponent.fill(poseStack, x - radius, cy - radius, x + radius + 1, cy + radius + 1, color);
    }

    private static void drawLabels(Font font, PoseStack poseStack, Marker closest, int left, int cy) {
        int textY = cy - 4;

        StringBuilder leftText = new StringBuilder();
        if (LocatorConfig.SHOW_NAME.get()) {
            leftText.append(closest.player.getGameProfile().getName());
        }
        if (LocatorConfig.SHOW_DISTANCE.get()) {
            if (leftText.length() > 0) {
                leftText.append(' ');
            }
            leftText.append(Math.round(closest.distance)).append('m');
        }
        if (leftText.length() > 0) {
            String s = leftText.toString();
            font.drawShadow(poseStack, s, left - 4 - font.width(s), textY, TEXT_COLOR);
        }

        if (LocatorConfig.SHOW_HEIGHT.get()) {
            String yText = "Y " + Mth.floor(closest.y);
            int x = left + BAR_WIDTH + 4;
            font.drawShadow(poseStack, yText, x, textY, TEXT_COLOR);

            long diff = Math.round(closest.dy);
            if (diff != 0) {
                String arrow = (diff > 0 ? "▲" : "▼") + Math.abs(diff);
                font.drawShadow(poseStack, arrow, x + font.width(yText) + 3, textY, diff > 0 ? UP_COLOR : DOWN_COLOR);
            }
        }
    }

    /** Feste Farbe pro Spieler, abgeleitet aus der UUID, damit man Spieler auseinanderhalten kann. */
    private static int colorFor(AbstractClientPlayer player) {
        float hue = (player.getUUID().hashCode() & 0xFFFF) / 65536f;
        return Mth.hsvToRgb(hue, 0.65f, 1.0f) & 0x00FFFFFF;
    }

    private static final class Marker {
        final AbstractClientPlayer player;
        final int x;
        final double distance;
        final double y;
        final double dy;
        final boolean inView;

        Marker(AbstractClientPlayer player, int x, double distance, double y, double dy, boolean inView) {
            this.player = player;
            this.x = x;
            this.distance = distance;
            this.y = y;
            this.dy = dy;
            this.inView = inView;
        }
    }
}
