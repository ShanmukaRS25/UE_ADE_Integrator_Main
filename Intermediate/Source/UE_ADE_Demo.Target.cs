using UnrealBuildTool;

public class UE_ADE_DemoTarget : TargetRules
{
	public UE_ADE_DemoTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Game;
		ExtraModuleNames.Add("UE_ADE_Demo");
	}
}
