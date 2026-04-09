using UnrealBuildTool;

public class UE_ADE_DemoClientTarget : TargetRules
{
	public UE_ADE_DemoClientTarget(TargetInfo Target) : base(Target)
	{
		DefaultBuildSettings = BuildSettingsVersion.Latest;
		IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
		Type = TargetType.Client;
		ExtraModuleNames.Add("UE_ADE_Demo");
	}
}
