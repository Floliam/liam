package com.floliam.dragonfinder;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.fml.DistExecutor;
import net.minecraftforge.fml.IExtensionPoint;
import net.minecraftforge.fml.ModLoadingContext;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.config.ModConfig;
import net.minecraftforge.network.NetworkConstants;

@Mod(DragonFinder.MOD_ID)
public class DragonFinder {
    public static final String MOD_ID = "dragonfinder";

    public DragonFinder() {
        ModLoadingContext context = ModLoadingContext.get();

        // Rein clientseitig: Server müssen die Mod nicht haben, und sie verlangt sie auch nicht.
        context.registerExtensionPoint(IExtensionPoint.DisplayTest.class,
                () -> new IExtensionPoint.DisplayTest(() -> NetworkConstants.IGNORESERVERONLY, (remote, isServer) -> true));

        context.registerConfig(ModConfig.Type.CLIENT, FinderConfig.SPEC);

        DistExecutor.unsafeRunWhenOn(Dist.CLIENT, () -> ClientSetup::init);
    }
}
