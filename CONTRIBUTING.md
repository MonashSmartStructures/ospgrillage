# Contributing to ospgrillage

We welcome contribution towards *ospgrillage*. 
When contributing to this repository, please first discuss the change you wish to make via issue, email, 
or any other method with the owners of this repository before making a change.

Please note we have a code of conduct, please follow it in all your interactions with the project.

## Code of conduct

Please read and follow our [Code of Conduct][coc].

## <a name="question"></a> Questions or Problems

We are happy to answer your questions or help with any problems you have with *ospgrillage*. 
Do [submit an issue](https://github.com/MonashSmartStructures/ospgrillage/issues) to *ospgrillage*'s repository.

## <a name="issue"></a> Bug reports

If you find a bug in the source code, you can help us by [submitting an issue](#submit-issue) to *ospgrillage* repository.
If you have a fix for bugs, you can [submit a Pull Request](#submit-pr) for it.


## <a name="feature"></a> Contributing a new feature
We love to hear your ideas on new features for *ospgrillage*. If you like to implement a 
new feature, please [submit an issue](https://github.com/MonashSmartStructures/ospgrillage/issues)
on this. First outline your proposal so that it can be discussed. This allow us to 
better coordinate our efforts, prevent duplication of work, and provide feedback on your ideas of features.



## <a name="commit"></a> Commit Message Format

*ospgrillage* adopts a commit message format that is similar to [Angular](https://github.com/angular/angular/blob/master/CONTRIBUTING.md#commit).
We strongly-advice you refer to them for all commits. 

The commit message requires a `header` and `body`. 

```
<header>
<BLANK LINE>
<body>
```
### Header

The `header` is mandatory and must conform to the following format similar to Angular.

```
<type>(<scope>): <short summary>
```

where `<type>` must be one of the following:

* **build** : Changes affecting build system
* **docs**: Changes to documentation only
* **ci**: Changes to continuous integration scripts or system
* **feat**: Change/add new feature
* **fix**: Bug fixing
* **perf**: Changes related to package performance
* **refactor**: Changes other than bug fixes or features
* **test**: Addition/modification to tests

`<scope>` can be one of the following:

[to add scope]

`<short summary>` to provide description of change. 

* use present tense: e.g. "change" not "changed"
* no dot (.) at end
* first letter lowercase

### Body

Similar to `<short summary>` use the imperative, present tense: e.g. "fix" but not "fixed" nor "fixing".

`<body>` should contain explanation for the change in commit message. For example, explaining *why* the changes is being made.
